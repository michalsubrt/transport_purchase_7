from openerp.osv import fields, osv
from openerp.tools.translate import _


class purchase_order_fleet_vehicle(osv.osv):
    _name = 'purchase.order.fleet_vehicle'
    _description = 'All purchases order and associated vehicles'
    _columns = {
                'purchase_order_id': fields.many2one(obj='purchase.order', string='Purchase Order', 
                 ondelete='cascade'),
                'purchases_date': fields.date(string='Purchases Date'),
                'partner_departure_id': fields.many2one(obj='res.partner', string='From'),
                'partner_destination_id': fields.many2one(obj='res.partner', string='To'),
                'delivery_date': fields.date(string='Delivery Date',
                                          help='The date that will start to transport'),       
                'return_date': fields.date(string='Return Date',
                                          help='The expected date to finish all the transport'),
                'fleet_vehicle_id': fields.many2one(obj='fleet.vehicle', string='Vehicle', required=True,
                                          ondelete='restrict'),             
                'license_plate': fields.char('License Plate', size=64, required=False, store=True),            
                'internal_number': fields.integer('Number'),
                'employee_driver_id': fields.many2one(obj='hr.employee', string='Driver', required=True,
                                               ondelete='restrict'),
                'employee_helper_id': fields.many2one(obj='hr.employee', string='helper', required=False,
                                               ondelete='restrict'),
                'fleet_trailer_id': fields.many2one(obj='fleet.vehicle', string='Trailer',
                                               ondelete='restrict', required=True),
                'trailer_license_plate': fields.char(string='Trailer License Plate', size=64, required=False, store=True),
                'cargo_ids': fields.one2many(obj='purchase.order.cargo', fields_id='purchase_order_fleet_id', 
                                         string='Cargo', required=True,
                                         help=_('All purchase transported cargo')),                                
                }      
      
    def fleet_trailer_id_change(self, cr, uid, ids, fleet_trailer_id):
        result={}
        
        if not fleet_trailer_id:
            return {'value': result}
        
        trailer = self.pool.get('fleet.vehicle').browse(cr, uid, fleet_trailer_id)
        
        if trailer:
            result['trailer_license_plate'] = trailer.license_plate
            
        return {'value': result}      
      
    def fleet_vehicle_id_change(self, cr, uid, ids,fleet_vehicle_id, context):
        result={}
        
        if not fleet_vehicle_id:
            return {'value': result}
                            
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, fleet_vehicle_id)                           
        purchase_order = self.pool.get('purchase.order').browse(cr, uid, context.get('purchase_order_id')) 
                           
        if vehicle:
            result['license_plate'] =  vehicle.license_plate
            result['employee_driver_id'] = vehicle.emp_driver_id.id            
            result['internal_number'] = vehicle.internal_number
        
            print purchase_order      
      
        if purchase_order:
            #print "purchase_date=" + purchase_order.date_order
            result['purchase_date'] =  purchase_order.date_order
            #print "purchase departure id=" + purchase_order.partner_departure_id.id
            result['partner_departure_id'] =  purchase_order.partner_departure_id.id
            #print "purchase shipping id=" + purchase_order.partner_shipping_id.id
            result['partner_destination_id'] =  purchase_order.partner_shipping_id.id
            #print "deli date=" + purchase_order.delivery_date 
            result['delivery_date'] =  purchase_order.delivery_date
            #print "deli date=" + purchase_order.return_dae
            result['return_date'] =  purchase_order.return_date    

            return {'value':result}      

    def copy(self, cr, uid, _id, default=None, context=None):
        
        if not default:
            default = {}
            default.update({            
            'state': 'draft',            
         })
        return super(purchase_order_fleet_vehicle, self).copy(cr, uid, _id, default, context=context)
             
#     _sql_constraints = [('vehicle_uniq', 'unique(fleet_vehicle_id,purchase_order_id)',
#                          'Vehicle must be unique per purchase order! Remove the duplicate vehicle'),
#                         ('employee_unique','unique(employee_driver_id,purchase_order_id)',
#                          'A driver must be unique per purchase order! Remove the duplicate driver'),]  
         
purchase_order_fleet_vehicle()      

class purchase_order_cargo(osv.osv):
    _name = 'purchase.order.cargo'
    _description = 'Transport cargo from a purchase order transport service'
    _columns = {
            'purchase_order_fleet_id':fields.many2one(obj='purchase.order.fleet_vehicle', string='Purchase Order Vehicle',
                                            ondelete='cascade', required=True,readonly=True),            
            'transport_date': fields.date(string='Transport Date', required=True,
                                          help=_('The day when the product was transported.')),           
            'cargo_product_id':fields.many2one(obj='product.product', string='Cargo', required=True),                
            'cargo_docport':fields.char(string='Port Document', size=64, required=False, readonly=False,
                                        help=_('Associated port document of the transported product if applicable.')),
            'brand':fields.char('Brand', size=64, required=False, readonly=False,
                                help=_('Brand of the transported product if applicable.')),
            'model':fields.char('Model', size=64, required=False, readonly=False,
                                help=_('Model of the transported product if applicable.')),
            'cargo_ident':fields.char('Identification', size=64, required=False, readonly=False,
                                      help=_('Identification of the cargo.Ex:Id,License Plate,Chassi')),
            'purchase_order_id':fields.many2one(obj='purchase.order', string='Purchase Order', required=True),
            'transport_from_id': fields.many2one(obj='res.partner', string='From'),
            'transport_to_id': fields.many2one(obj='res.partner', string='To'),
                    }
                  
    def cargo_id_change(self,cr,uid,ids,cargo_product_id,context):
        
        result={}      
        if not cargo_product_id:
            return {'value':result}
                        
        purchase_order = self.pool.get('purchase.order').browse(cr,uid,context.get('purchase_order_id')) 
        
        if purchase_order:
            result['purchase_order_id'] = context.get('purchase_order_id')
            
#             if [ product purchase_order_fleet_idfor product in purchase_order.order_line if cargo_product_id == product.product_id]:            
    
        return {'value':result}  
        
    def copy(self, cr, uid, _id, default=None, context=None): 
        
        if not default:

            default = {}
#         default.update({
#         })
        
        res_id = super(purchase_order_cargo, self).copy(cr, uid, _id, default, context)
        return res_id
        
class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    #Do not touch _name it must be same as _inherit
    #_name = 'purchase.order'
    _columns = {
            'fleet_vehicles_ids':fields.one2many(obj='purchase.order.fleet_vehicle',
                                                 fields_id='purchase_order_id',string='Transport Vehicles',
                                                 required=True),
            'partner_departure_id':fields.many2one('res.partner', string='From', required=True),           
            'delivery_date': fields.date('Transport Start',required=True,
                                         help=_('Expected Transport start date.')),
            'return_date':fields.date('Transport Finish',required=True,
                                      help=_('Expected Transport finish date.')),
            'cargo_ids':fields.one2many(obj='purchase.order.cargo', fields_id='purchase_order_id', 
                                        string='Cargo Manifest', required=False,
                                        help=_('All transported cargo manifest.')),             
                    }        
 
    def _validate_data(self, cr, uid, ids):
        for dates in self.browse(cr,uid,ids):
            if dates.return_date < dates.delivery_date:
                return False            
            else:
                return True
    #TODO : check condition and return boolean accordingly
    
    def _validate_cargo_products(self,cr,uid,ids):
         
        result = True
        cargo_products_ids = []        
        purchase_order = self.browse(cr,uid,ids[0])
        
        if purchase_order:            
            cargo_products_ids = [cargo.cargo_product_id.id for cargo in purchase_order.cargo_ids]
            
            if not cargo_products_ids:
                result = True
            else:                
                line_products_ids = [line.product_id.id for line in purchase_order.order_line]
                result = set(cargo_products_ids) == set(line_products_ids)
                            
        return result 

    def _validate_cargo_products_qty(self,cr,uid,ids):
        
        result = True
        msg_format=""
        line_product_ids = []
        line_product_qts = []
        
        purchase_order = self.browse(cr,uid,ids[0])
        
        if purchase_order:            
            cargo_product_ids = [cargo.cargo_product_id.id for cargo in purchase_order.cargo_ids]
            
            #give all products for order line
            line_product_ids = [line.product_id.id for line in purchase_order.order_line]
            line_product_qts = [line.product_uom_qty for line in purchase_order.order_line]
            
            line_product_ids_qts = {}
            line_product_dif_ids = {}
            
            for idx,prod_id in enumerate(line_product_ids):                
                if prod_id in line_product_ids_qts.keys():
                    line_product_ids_qts[prod_id]+= line_product_qts[idx]
                else:
                    line_product_ids_qts[prod_id] = line_product_qts[idx]                            
                        
            if not cargo_product_ids:
                result = True
            else:
                for cargo_product_id in set(cargo_product_ids):                                    
                    line_product_ids_dict = { prod_id:qtd  for prod_id,qtd in line_product_ids_qts.iteritems() 
                                         if prod_id == cargo_product_id 
                                         and int(line_product_ids_qts[prod_id]) != cargo_product_ids.count(cargo_product_id)}  
                    
                    line_product_dif_ids.update(line_product_ids_dict)
                                                   
                if len(line_product_dif_ids) > 0:
                    
                    line_product_names = self.pool.get('product.product').name_get(cr,uid,line_product_dif_ids.keys(),context=None)
                    cargo_product_qts = [ cargo_product_ids.count(cargo_product_id) for cargo_product_id in line_product_dif_ids.keys()]
                    for product_name in line_product_names:
                        index= line_product_names.index(product_name)
                        
                        msg_format =  _("""Product:%s\n\tOrder=%s vs Cargo=%s\n""") % (product_name[1],
                                                                                       int(line_product_dif_ids[product_name[0]]),
                                                                                       cargo_product_qts[index])
                                                             
                    message = _("""The following products quantities in cargo don't match\n quantities in purchase order line:\n%s
                                    """) % (msg_format)
                        
                    raise osv.except_osv(_('Error'), message)
                    result = False
                else:
                    result = True
        return result
    
    _constraints = [(_validate_data,'Error: Invalid return date', ['delivery_date','return_date']),
                    (_validate_cargo_products,"Error: There is a cargo product that doesn't belongs to the purchase order line!",['cargo_ids','order_line']),
                    (_validate_cargo_products_qty,"Error: In products quantities",['cargo_ids','order_line'])]
 
purchase_order()  

class fleet_vehicle(osv.osv):
    _inherit = 'fleet.vehicle' 
    #Do not touch _name it must be same as _inherit
    #_name = 'fleet.vehicle'
    _columns = {
            'purchases_order_ids':fields.one2many(obj='purchase.order.fleet_vehicle',
                                              fields_id='fleet_vehicle_id', string='Vehicle purchases'),
            'internal_number': fields.integer(string='Internal Number'),
            'is_trailer':fields.boolean(string='Is Trailer',required=False),
                    }
fleet_vehicle()

class hr_employee_driver_purchases(osv.osv):
    _inherit = 'hr.employee' 
    #Do not touch _name it must be same as _inherit
    #_name = 'hr.employee'
      
    _columns = {
            'purchases_order_ids':fields.one2many(obj='purchase.order.fleet_vehicle',
                                               fields_id='employee_driver_id', string='Driver purchases'),
            'is_driver':fields.boolean('Is Driver', required=False),
                    }        
        
hr_employee_driver_purchases()                                       
